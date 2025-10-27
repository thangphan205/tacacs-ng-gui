import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { type ApiError, type ProfileScriptPublic, ProfilescriptsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditProfileScriptProps {
  profilescript: ProfileScriptPublic
}

interface ProfileScriptUpdateForm {
  condition: string;
  key: string;
  value: string;
  action: string;
  description?: (string | null);
  profile_id?: (string | null);
}

const EditProfileScript = ({ profilescript }: EditProfileScriptProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProfileScriptUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      ...profilescript,
      description: profilescript.description ?? undefined,
      key: profilescript.key ?? undefined,
      value: profilescript.value ?? undefined,
      action: profilescript.action ?? undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ProfileScriptUpdateForm) =>
      ProfilescriptsService.updateProfilescript({ id: profilescript.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("ProfileScript updated successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["profilescripts"] })
    },
  })

  const onSubmit: SubmitHandler<ProfileScriptUpdateForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit ProfileScript
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit ProfileScript</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the item details below.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.key}
                errorText={errors.key?.message}
                label="Key"
              >
                <Input
                  {...register("key", {
                    required: "Key is required.",
                  })}
                  placeholder="Key"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.value}
                errorText={errors.value?.message}
                label="value"
              >
                <Input
                  {...register("value", {
                    required: "value is required.",
                  })}
                  placeholder="value"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.action}
                errorText={errors.action?.message}
                label="action"
              >
                <Input
                  {...register("action", {
                    required: "action is required.",
                  })}
                  placeholder="action"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Input
                  {...register("description")}
                  placeholder="Description"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" loading={isSubmitting}>
                Save
              </Button>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditProfileScript
