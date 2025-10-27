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

import { type ProfileScriptSetCreate, ProfilescriptsetsService } from "@/client"
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

const AddProfileScriptSet = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<ProfileScriptSetCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      key: "",
      description: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ProfileScriptSetCreate) =>
      ProfilescriptsetsService.createProfilescriptset({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("ProfileScriptSet created successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["profilescriptsets"] })
    },
  })

  const onSubmit: SubmitHandler<ProfileScriptSetCreate> = (data) => {
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
          Add ProfileScriptSet
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Add ProfileScriptSet</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Fill in the details to add a new item.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.profilescript_id}
                errorText={errors.profilescript_id?.message}
                label="profilescript_id"
              >
                <Input
                  {...register("profilescript_id", {
                    required: "profilescript_id is required.",
                  })}
                  placeholder="profilescript_id"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.key}
                errorText={errors.key?.message}
                label="key"
              >
                <Input
                  {...register("key", {
                    required: "key is required.",
                  })}
                  placeholder="key"
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

export default AddProfileScriptSet
