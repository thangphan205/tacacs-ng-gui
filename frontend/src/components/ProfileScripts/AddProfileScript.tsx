import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaPlus } from "react-icons/fa"

import { type ProfileScriptCreate, ProfilescriptsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddProfileScript = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<ProfileScriptCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      key: "",
      value: "",
      description: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ProfileScriptCreate) =>
      ProfilescriptsService.createProfilescript({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("ProfileScript created successfully.")
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

  const onSubmit: SubmitHandler<ProfileScriptCreate> = (data) => {
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
        <Button value="add-item" my={4}>
          <FaPlus fontSize="16px" />
          Add ProfileScript
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Add ProfileScript</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Fill in the details to add a new item.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.condition}
                errorText={errors.condition?.message}
                label="condition"
              >
                <Input
                  {...register("condition", {
                    required: "condition is required.",
                  })}
                  placeholder="condition"
                  type="text"
                />
              </Field>
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
                invalid={!!errors.profile_id}
                errorText={errors.profile_id?.message}
                label="profile_id"
              >
                <Input
                  {...register("profile_id", {
                    required: "profile_id is required.",
                  })}
                  placeholder="profile_id"
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
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              Save
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddProfileScript
